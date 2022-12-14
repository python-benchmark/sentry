import styled from '@emotion/styled';
import classNames from 'classnames';

import DeprecatedDropdownMenu from 'sentry/components/deprecatedDropdownMenu';
import {IconEllipsis} from 'sentry/icons';

const ContextMenu = ({children}) => (
  <DeprecatedDropdownMenu>
    {({isOpen, getRootProps, getActorProps, getMenuProps}) => {
      const topLevelCx = classNames('dropdown', {
        'anchor-right': true,
        open: isOpen,
      });

      return (
        <MoreOptions
          {...getRootProps({
            className: topLevelCx,
          })}
        >
          <DropdownTarget
            {...getActorProps<HTMLDivElement>({
              onClick: (event: React.MouseEvent) => {
                event.stopPropagation();
                event.preventDefault();
              },
            })}
          >
            <IconEllipsis data-test-id="context-menu" size="md" />
          </DropdownTarget>
          {isOpen && (
            <ul {...getMenuProps({})} className={classNames('dropdown-menu')}>
              {children}
            </ul>
          )}
        </MoreOptions>
      );
    }}
  </DeprecatedDropdownMenu>
);

const MoreOptions = styled('span')`
  display: flex;
  color: ${p => p.theme.textColor};
`;

const DropdownTarget = styled('div')`
  display: flex;
  cursor: pointer;
  padding: 0 5px;
`;

export default ContextMenu;
